import unittest
from backend.providers.base import ProviderStatus
from backend.router.auto_router import AutoRouter
from backend.services.provider_health import ProviderHealthService, ProviderHealthState
class ProviderHealthTests(unittest.TestCase):
 def test_health_distinguishes_unavailable_and_degraded(self):
  service=ProviderHealthService(); self.assertEqual(service.assess(ProviderStatus("p",False,"offline",[]),False).state,ProviderHealthState.UNAVAILABLE); self.assertEqual(service.assess(ProviderStatus("p",True,"ok",[]),False).state,ProviderHealthState.DEGRADED)
 def test_auto_skips_degraded_model(self):
  models={"terra":{"availability":True,"routing_available":False,"supported_reasoning_efforts":["medium"],"default_reasoning_effort":"medium"},"deepseek":{"availability":True,"routing_available":True,"supported_reasoning_efforts":["low"],"default_reasoning_effort":"low"}}; self.assertEqual(AutoRouter.decide("复杂代码设计",0,models).selection_key,"deepseek")
if __name__=="__main__": unittest.main()