
# Robustly pulls TransformerMeshImpedance r/x (pu), maps to ends, and prints ohmic + pu values.
from rdflib import Graph, RDF, URIRef
from math import sqrt, atan2, degrees

CIM_FILE    = "simple_cim.rdf"
SBASE_KVA   = 1000.0
RATEDU_IS_LL = True

g = Graph()
g.parse(CIM_FILE)

def endswith_pred(p: URIRef, tail: str) -> bool:
    return str(p).endswith(tail)

def zbase_ohm(kv_ll: float, sbase_kva: float) -> float:
    # Base impedance per phase (using line-line kV): Zb = (kV_LL^2) / MVA
    return (kv_ll ** 2) / (sbase_kva / 1000.0)


ends_ratedU = {}
q_rated = """
SELECT ?end ?p ?u WHERE {
  ?end a ?t .
  FILTER regex(str(?t), "TransformerEnd$")
  ?end ?p ?u .
  FILTER regex(str(?p), "TransformerEnd.ratedU$")
}
"""
for end, p, u in g.query(q_rated):
    ends_ratedU[str(end)] = float(u)

print("TransformerEnds ratedU (kV):", ends_ratedU)

# ratedU is actually line-to-neutral, convert to L-L for base impedance calc
if not RATEDU_IS_LL:
    ends_ratedU = {k: (v * sqrt(3.0)) for k, v in ends_ratedU.items()}

meshes = []
for subj, typ in g.subject_objects(RDF.type):
    if str(typ).endswith("TransformerMeshImpedance"):
        # Gather properties from triples
        info = {"uri": str(subj)}
        for p, o in g.predicate_objects(subj):
            ps = str(p)
            if ps.endswith("TransformerMeshImpedance.r"):
                info["r_pu"] = float(o)
            elif ps.endswith("TransformerMeshImpedance.x"):
                info["x_pu"] = float(o)
            elif ps.endswith("fromTransformerEnd"):
                info["from_end"] = str(o)
            elif ps.endswith("toTransformerEnd"):
                info["to_end"] = str(o)
        meshes.append(info)

if not meshes:
    print("No TransformerMeshImpedance objects found. ")
    raise SystemExit

#Printing
for m in meshes:
    r_pu = m.get("r_pu")
    x_pu = m.get("x_pu")
    f_end = m.get("from_end")
    t_end = m.get("to_end")
    print(f"\nImpedance {m['uri']}: r_pu={r_pu:.6f}, x_pu={x_pu:.6f}")

    def report_for_end(end_uri: str, label: str):
        kv = ends_ratedU.get(end_uri)
        if kv is None:
            print(f"  [{label}] Missing ratedU for end {end_uri}")
            return
        zb = zbase_ohm(kv, SBASE_KVA)
        R_ohm = r_pu * zb
        X_ohm = x_pu * zb
        Zmag_pu = sqrt(r_pu**2 + x_pu**2)
        Zang_deg = degrees(atan2(x_pu, r_pu))
        xr = (x_pu / r_pu) if r_pu != 0 else float("inf")
        print(
            f"  [{label}] base={kv:.3f} kV_LL, Sbase={SBASE_KVA:.1f} kVA\n"
            f"    R_pu={r_pu:.6f}, X_pu={x_pu:.6f}, |Z|_pu={Zmag_pu:.6f}, ∠Z={Zang_deg:.2f}° , X/R={xr:.3f}\n"
            f"    R={R_ohm:.5f} Ω, X={X_ohm:.5f} Ω, |Z|={sqrt(R_ohm**2 + X_ohm**2):.5f} Ω"
        )

    report_for_end(f_end, "FROM")
    report_for_end(t_end, "TO")
