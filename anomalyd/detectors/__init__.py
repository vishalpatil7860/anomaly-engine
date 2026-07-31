from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class AnomalyEvent:
    table: str
    column: Optional[str]
    anomaly_type: str
    severity: str
    observed_value: Any
    expected_range: Optional[str]
    explanation: Optional[str]
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

class BaseDetector:
    type: str = "base"
    def __init__(self, config):
        self.config = config
    def detect(self, df, baseline=None):
        raise NotImplementedError