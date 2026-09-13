"""Local deterministic provider health classification for router decisions."""
from dataclasses import dataclass
from enum import StrEnum
from backend.providers.base import ProviderStatus
class ProviderHealthState(StrEnum): HEALTHY="healthy"; DEGRADED="degraded"; UNAVAILABLE="unavailable"
@dataclass(frozen=True)
class ProviderHealth: state: ProviderHealthState; message: str; routing_available: bool
class ProviderHealthService:
    def assess(self,status:ProviderStatus,model_available:bool)->ProviderHealth:
        if not status.available: return ProviderHealth(ProviderHealthState.UNAVAILABLE,status.message,False)
        if not model_available: return ProviderHealth(ProviderHealthState.DEGRADED,"Provider 已响应，但当前没有可路由的模型。",False)
        return ProviderHealth(ProviderHealthState.HEALTHY,status.message,True)
provider_health_service=ProviderHealthService()