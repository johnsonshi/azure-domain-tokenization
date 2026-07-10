---
title: Automation reference
ms.service: automation
---

# Automate deployments with PowerShell and Bicep

Use the `Get-AzResourceGroup` cmdlet to list resource groups.

```powershell
Get-AzResourceGroup -Name "myGroup" | Select-Object ResourceGroupName, Location
New-AzResourceGroup -Name "myGroup" -Location "eastus2"
```

Define infrastructure with Bicep:

```bicep
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  sku: {
    name: 'Premium'
  }
}
```

Pipeline configuration:

```yaml
trigger:
  branches:
    include:
      - main
pool:
  vmImage: ubuntu-latest
```

Set the environment variable `AZURE_SUBSCRIPTION_ID` before running the script.
