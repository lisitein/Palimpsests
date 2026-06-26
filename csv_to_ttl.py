#!/usr/bin/env python3
"""
csv_to_ttl.py  (v3)
Convert the intertextual-operations CSV into RDF/Turtle for Protege.

Model (per the user's specification):
  - Each row is ONE operation individual, typed directly as one
    CreativeStrategy subclass (Imitation | Transformation | Inheritance).
    There is NO separate TransformativeOperation umbrella class.
  - The operation transforms the OriginalWork's :sourceElement individual
    into the TransformativeWork's :targetElement individual; both are
    individuals of the SAME NarrativeElement class (:actsOnElement).
  - For Inheritance, source and target are the SAME individual (carried over).
  - rationale + externalRef are annotation properties.
  - Works are typed :Work, declared owl:equivalentClass creon:CreativeProduct
    (IRI reference only; creon is NOT imported).
  - hypo/hyper is not a class; it is which property points at the work.
"""
import csv, re, sys, unicodedata

BASE  = "http://example.org/palimpsests#"
CREON = "http://www.ontologydesignpatterns.org/ont/creativity/creon.owl#"
in_path = "Operations_Audited.csv"
out_path = "output1.ttl"

def local_name(text):
    if not text: return None
    text = text.strip()
    if not text: return None
    text = unicodedata.normalize("NFKC", text).replace("&", "and")
    text = re.sub(r"[^\w]", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text: return None
    if text[0].isdigit(): text = "n_" + text
    return text

def esc_literal(text):
    if text is None: text = ""
    return (text.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n").replace("\r",""))

def is_http(uri):
    return bool(uri) and uri.strip().lower().startswith("http")

NARRATIVE_TREE = {
    "Character": None,
    "CharacterIdentity":"Character","CharacterArc":"Character","CharacterFunction":"Character",
    "BackgroundSetting": None,
    "Chronotope":"BackgroundSetting","WorldRules":"BackgroundSetting",
    "StoryStructure": None,
    "EventSequence":"StoryStructure","Causality":"StoryStructure",
    "Outcome":"StoryStructure","Focalization":"StoryStructure",
    "Relation": None,
    "RelationType":"Relation","RelationTopology":"Relation",
    "ContentDomain": None,
    "MediumType": None,
}
CREATIVE_STRATEGIES = ["Imitation","Transformation","Inheritance"]

def main(in_path, out_path):
    with open(in_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    works={}; elements={}; used_narr=set(); op_blocks=[]
    element_works={}   # element_ln -> set of work_ln it belongs to

    def reg_work(label, uri):
        ln = local_name(label)
        if not ln: return None
        if ln not in works:
            works[ln]={"label":label.strip(),"ref":uri.strip() if is_http(uri) else None}
        elif is_http(uri) and not works[ln]["ref"]:
            works[ln]["ref"]=uri.strip()
        return ln

    def reg_element(value, narr_class, work_ln=None):
        ln = local_name(value)
        if not ln: return None
        nc = local_name(narr_class) or "NarrativeElement"
        elements[ln]=nc; used_narr.add(nc)
        if work_ln:
            element_works.setdefault(ln, set()).add(work_ln)
        return ln

    for r in rows:
        op_inst=(r.get("operation: instance") or "").strip()
        if not op_inst: continue
        strategy=(r.get("CreativeStrategy (Class)") or "").strip()
        tw=(r.get("Transformative_Work") or "").strip()
        twu=(r.get("Transformative_Work_URI") or "").strip()
        ow=(r.get("Original_Work") or "").strip()
        owu=(r.get("Original_Work_URI") or "").strip()
        src=(r.get("SourceElement") or "").strip()
        tgt=(r.get("TargetElement") or "").strip()
        narr=(r.get("NarrativeElement (Class)") or "").strip()
        ann=(r.get("Rationale_Annotation") or "").strip()

        op_ln=local_name(op_inst)
        strat_ln=local_name(strategy) if strategy else None
        tw_ln=reg_work(tw,twu) if tw else None
        ow_ln=reg_work(ow,owu) if ow else None
        src_ln=reg_element(src,narr,ow_ln) if src else None
        tgt_ln=reg_element(tgt,narr,tw_ln) if tgt else None
        narr_ln=local_name(narr) if narr else None
        if narr_ln: used_narr.add(narr_ln)

        lines=[f":{op_ln} rdf:type owl:NamedIndividual , :{strat_ln} ;"]
        if ow_ln:  lines.append(f"    :hasOriginalWork :{ow_ln} ;")
        if tw_ln:  lines.append(f"    :hasTransformativeWork :{tw_ln} ;")
        if narr_ln:lines.append(f"    :actsOnElement :{narr_ln} ;")
        if src_ln: lines.append(f"    :sourceElement :{src_ln} ;")
        if tgt_ln: lines.append(f"    :targetElement :{tgt_ln} ;")
        lines.append(f'    rdfs:label "{esc_literal(op_inst)}" ;')
        if ann:    lines.append(f'    :rationale "{esc_literal(ann)}" ;')
        lines[-1]=lines[-1].rstrip(" ;")+" ."
        op_blocks.append("\n".join(lines))

    o=[]
    o.append("@prefix :     <%s> ."%BASE)
    o.append("@prefix creon: <%s> ."%CREON)
    o.append("@prefix owl:  <http://www.w3.org/2002/07/owl#> .")
    o.append("@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    o.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    o.append("@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .")
    o.append("")
    o.append("<%s> rdf:type owl:Ontology ."%BASE.rstrip("#"))
    o.append("")
    o.append("### Creative-strategy classes (these three carry all the strategy semantics)")
    o.append(":CreativeStrategy rdf:type owl:Class .")
    for s in CREATIVE_STRATEGIES:
        o.append(":%s rdf:type owl:Class ; rdfs:subClassOf :CreativeStrategy ."%s)
    o.append("")
    o.append("### Narrative-element classes")
    o.append(":NarrativeElement rdf:type owl:Class .")
    for cls,parent in NARRATIVE_TREE.items():
        p=parent if parent else "NarrativeElement"
        o.append(":%s rdf:type owl:Class ; rdfs:subClassOf :%s ."%(cls,p))
    for nc in sorted(used_narr):
        if nc not in NARRATIVE_TREE and nc!="NarrativeElement":
            o.append(":%s rdf:type owl:Class ; rdfs:subClassOf :NarrativeElement ."%nc)
    o.append("")
    o.append("### Work class — reuses creon:CreativeProduct via equivalentClass (creon not imported)")
    o.append(":Work rdf:type owl:Class ; owl:equivalentClass creon:CreativeProduct .")
    o.append("")
    o.append("### Object properties")
    for p,dom,rng in [
        ("hasOriginalWork","CreativeStrategy","Work"),
        ("hasTransformativeWork","CreativeStrategy","Work"),
        ("actsOnElement","CreativeStrategy","NarrativeElement"),
        ("sourceElement","CreativeStrategy","NarrativeElement"),
        ("targetElement","CreativeStrategy","NarrativeElement"),
    ]:
        o.append(":%s rdf:type owl:ObjectProperty ; rdfs:domain :%s ; rdfs:range :%s ."%(p,dom,rng))
    o.append(":elementOfWork rdf:type owl:ObjectProperty ; rdfs:domain :NarrativeElement ; rdfs:range :Work ; owl:inverseOf :hasNarrativeElement .")
    o.append(":hasNarrativeElement rdf:type owl:ObjectProperty ; rdfs:domain :Work ; rdfs:range :NarrativeElement .")
    o.append("")
    o.append("### Annotation properties")
    o.append(':rationale rdf:type owl:AnnotationProperty ; rdfs:label "rationale" .')
    o.append(':externalRef rdf:type owl:AnnotationProperty ; rdfs:label "external reference" .')
    o.append("")
    o.append("### Works")
    for ln,e in sorted(works.items()):
        b=[':%s rdf:type owl:NamedIndividual , :Work ;'%ln,
           '    rdfs:label "%s" ;'%esc_literal(e["label"])]
        if e["ref"]: b.append('    :externalRef "%s" ;'%esc_literal(e["ref"]))
        b[-1]=b[-1].rstrip(" ;")+" ."
        o.append("\n".join(b))
    o.append("")
    o.append("### Narrative-element instances (source / target values), linked to their work(s)")
    for ln,nc in sorted(elements.items()):
        wks = sorted(element_works.get(ln, []))
        line = ':%s rdf:type owl:NamedIndividual , :%s ; rdfs:label "%s"'%(ln,nc,esc_literal(ln))
        for w in wks:
            line += ' ;\n    :elementOfWork :%s'%w
        line += " ."
        o.append(line)
    o.append("")
    o.append("### Operations")
    for b in op_blocks:
        o.append(b); o.append("")

    with open(out_path,"w",encoding="utf-8") as f:
        f.write("\n".join(o))
    print("Wrote",out_path)
    print("  operations:",len(op_blocks))
    print("  works:",len(works))
    print("  element individuals:",len(elements))

if __name__=="__main__":
    main(in_path,out_path)