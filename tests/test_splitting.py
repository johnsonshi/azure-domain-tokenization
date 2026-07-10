"""Group-aware split isolation (plan.md §23)."""
from __future__ import annotations

from msdocs_tokenizer import splitting as sp
from msdocs_tokenizer.splitting import DocumentRef


def _make_docs():
    docs = []
    services = ["storage", "compute", "network", "aks", "functions", "cosmos-db",
                "monitor", "keyvault", "sql", "container-registry"]
    for svc in services:
        for i in range(20):
            docs.append(DocumentRef(
                document_id=f"{svc}-{i}",
                source_repo="MicrosoftDocs/azure-docs",
                source_path=f"articles/{svc}/page-{i}.md",
                cluster_id=-1,
            ))
    return docs


def test_all_docs_assigned_one_split():
    docs = _make_docs()
    asg = sp.assign_azure_splits(docs, seed=42)
    assert len(asg.doc_to_split) == len(docs)
    assert set(asg.doc_to_split.values()) <= {
        "azure_train", "azure_same_service_holdout", "azure_cross_service_holdout"
    }


def test_no_cross_split_leakage():
    docs = _make_docs()
    asg = sp.assign_azure_splits(docs, seed=42)
    violations = sp.verify_no_cross_split_leakage(docs, asg)
    assert violations == [], violations


def test_cross_service_holdout_service_disjoint_from_train():
    docs = _make_docs()
    asg = sp.assign_azure_splits(docs, seed=7)
    train_services = {
        sp.top_level_service(d.source_path)
        for d in docs if asg.doc_to_split[d.document_id] == "azure_train"
    }
    cross_services = {
        sp.top_level_service(d.source_path)
        for d in docs if asg.doc_to_split[d.document_id] == "azure_cross_service_holdout"
    }
    assert train_services.isdisjoint(cross_services)


def test_near_dup_cluster_not_split():
    # Two docs in same near-dup cluster in a train-eligible service must not
    # land in different splits.
    docs = [
        DocumentRef("d1", "r", "articles/storage/a.md", cluster_id=99),
        DocumentRef("d2", "r", "articles/storage/b.md", cluster_id=99),
        DocumentRef("d3", "r", "articles/storage/c.md", cluster_id=-1),
    ]
    # force storage into train by trying several seeds; invariant must always hold
    for seed in range(10):
        asg = sp.assign_azure_splits(docs, seed=seed)
        assert asg.doc_to_split["d1"] == asg.doc_to_split["d2"]
        assert sp.verify_no_cross_split_leakage(docs, asg) == []


def test_near_dup_cluster_spanning_services_not_split():
    # Regression: a near-dup cluster whose members live in DIFFERENT services
    # must never straddle train and any holdout (the real-data bug).
    docs = []
    services = ["storage", "compute", "network", "aks", "functions", "cosmos",
                "monitor", "keyvault", "sql", "cdn", "batch", "dns"]
    for svc in services:
        for i in range(15):
            docs.append(DocumentRef(f"{svc}-{i}", "r", f"articles/{svc}/p{i}.md", cluster_id=-1))
    # Inject cross-service near-dup clusters (same cluster id across two services)
    docs.append(DocumentRef("storage-x", "r", "articles/storage/x.md", cluster_id=500))
    docs.append(DocumentRef("compute-x", "r", "articles/compute/x.md", cluster_id=500))
    docs.append(DocumentRef("aks-y", "r", "articles/aks/y.md", cluster_id=501))
    docs.append(DocumentRef("dns-y", "r", "articles/dns/y.md", cluster_id=501))
    for seed in range(25):
        asg = sp.assign_azure_splits(docs, seed=seed)
        assert sp.verify_no_cross_split_leakage(docs, asg) == [], f"seed={seed}"
        # cluster-mates share a split
        assert asg.doc_to_split["storage-x"] == asg.doc_to_split["compute-x"]
        assert asg.doc_to_split["aks-y"] == asg.doc_to_split["dns-y"]



    assert sp.top_level_service("articles/storage/blobs/foo.md") == "storage"
    assert sp.top_level_service("docs/aks/bar.md") == "aks"


def test_deterministic():
    docs = _make_docs()
    a = sp.assign_azure_splits(docs, seed=1).doc_to_split
    b = sp.assign_azure_splits(docs, seed=1).doc_to_split
    assert a == b
