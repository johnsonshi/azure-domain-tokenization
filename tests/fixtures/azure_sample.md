---
title: Deploy a container to Azure
description: Sample doc for tests
ms.service: container-registry
author: contoso
---

# Deploy a container to Azure Container Registry

Azure Container Registry stores and manages container images. You can push an
image with the `az acr` command group. The resource provider is
`Microsoft.ContainerRegistry`.

<!-- This is a build directive that readers never see. -->

## Prerequisites

- An Azure subscription.
- The Azure CLI installed locally.

## Create a registry

Run the following command to create a registry:

```azurecli
az acr create --resource-group myGroup --name myRegistry --sku Premium
```

The registry endpoint will be `myregistry.azurecr.io`.

## Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| SKU | Premium | Supports geo-replication |
| Admin | Disabled | Use Microsoft Entra ID |

```json
{
  "sku": "Premium",
  "adminUserEnabled": false
}
```

For more information see https://learn.microsoft.com/azure/container-registry.
