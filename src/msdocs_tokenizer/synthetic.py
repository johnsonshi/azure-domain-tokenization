"""Synthetic diagnostic edge cases (plan.md §14). Diagnostic only — never the
primary evidence."""
from __future__ import annotations


def synthetic_edge_cases() -> list[tuple[str, str]]:
    """Return [(case_id, text)] covering the plan.md §14 edge categories."""
    cases: list[tuple[str, str]] = []

    def add(cid: str, text: str) -> None:
        cases.append((cid, text))

    # Azure resource-provider names
    for rp in ["Microsoft.ContainerRegistry/registries",
               "Microsoft.Storage/storageAccounts/blobServices",
               "Microsoft.Network/virtualNetworks/subnets",
               "Microsoft.ContainerService/managedClusters"]:
        add(f"rp:{rp}", rp)

    # CLI commands and flags
    for cmd in ["az acr create --resource-group myGroup --name myRegistry --sku Premium",
                "az aks get-credentials --resource-group rg --name cluster --overwrite-existing",
                "kubectl get pods --all-namespaces -o wide",
                "azcopy copy 'https://src.blob.core.windows.net' 'https://dst' --recursive"]:
        add(f"cli:{cmd[:24]}", cmd)

    # GUIDs
    for g in ["3f2504e0-4f89-41d3-9a0c-0305e82c3301",
              "00000000-0000-0000-0000-000000000000"]:
        add(f"guid:{g[:8]}", g)

    # URLs and paths
    for u in ["https://learn.microsoft.com/azure/container-registry/container-registry-intro",
              "myregistry.azurecr.io/samples/nginx:latest",
              "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{acct}"]:
        add(f"url:{u[:24]}", u)

    # Semantic versions
    for v in ["1.0.0", "2.31.0-preview.3", "v1.28.5", "3.12.13"]:
        add(f"ver:{v}", v)

    # JSON / YAML / Bicep / PowerShell / Bash
    add("json", '{"sku": {"name": "Premium"}, "adminUserEnabled": false, "tags": {"env": "prod"}}')
    add("yaml", "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\nspec:\n  replicas: 3")
    add("bicep", "resource r 'Microsoft.ContainerRegistry/registries@2023-07-01' = {\n  name: acrName\n  sku: { name: 'Premium' }\n}")
    add("powershell", "Get-AzResourceGroup -Name 'rg' | Select-Object ResourceGroupName, Location")
    add("bash", "for f in $(ls *.json); do az deployment group create --template-file $f; done")

    # Casing conventions
    add("camel", "resourceGroupName storageAccountName virtualMachineScaleSet")
    add("snake", "resource_group_name storage_account_name virtual_machine_scale_set")
    add("kebab", "resource-group-name storage-account-name virtual-machine-scale-set")

    # Unicode product names
    add("unicode", "Microsoft Entra ID · Azure Kubernetes Service · Cosmos DB — café 版本 🚀")

    # Empty / repeated / unusual whitespace / emoji
    add("empty", "")
    add("repeated", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    add("repeated_word", "token " * 40)
    add("whitespace", "a\t\tb\n\n\n   c    d\u00a0e")
    add("emoji", "✅ ❌ ⚠️ 🚀 🔥 📦 🌐 ☁️")

    return cases
