"""
Pure game logic — no UI toolkit imports.

Adaptive difficulty: ``engine.AdaptiveEngine`` / ``DifficultyProfile``.
"""

from .scoring import ScoreState, apply_hit
from .engine import (
    AdaptiveEngine,
    DifficultyProfile,
    build_profile,
    clamp_level,
    difficulty_label,
    n_back_depth,
)
from .difficulty import points_for_level, rate, set_size, time_ms, time_sec, session_pressure

from .focus import FocusEngine
from .memory import MemoryEngine
from .switch import SwitchEngine
from .speed import SpeedEngine
from .nback import NBackEngine
from .dual import DualNBackEngine
from .rotate import RotateEngine
from .stroop import StroopEngine
from .flanker import FlankerEngine
from .odd import OddEngine
from .trail import TrailEngine
from .span import SpanEngine
from .calc import CalcEngine
from .category import CategoryEngine
from .simon import SimonEngine
from .change import ChangeEngine
from .stop import StopEngine
from .digits import DigitsEngine
from .pasat import PasatEngine
from .track import TrackEngine
from .opspan import OspanEngine
from .sart import SartEngine
from .posner import PosnerEngine
from .symdigit import SymDigitEngine
from .dualtask import DualTaskEngine
from .rulesearch import RuleSearchEngine
from .rsvp import RsvpEngine
from .antisaccade import AntisaccadeEngine
from .running import RunningSpanEngine
from .tower import TowerEngine
from .conjunction import ConjunctionEngine
from .matrix import MatrixEngine
from .backward_span import BackwardSpanEngine
from .cpt import CptEngine
from .partial import PartialReportEngine
from .dichotic import DichoticEngine
from .prospective import ProspectiveEngine
from .loci import LociEngine
from .countkeep import CountKeepEngine
from .serial7 import Serial7Engine
from .cancel import CancellationEngine
from .oddball import OddballEngine
from .choicert import ChoiceRtEngine
from .wordlist import WordListEngine
from .brownpeterson import BrownPetersonEngine
ENGINES = {
    "focus": FocusEngine,
    "memory": MemoryEngine,
    "switch": SwitchEngine,
    "speed": SpeedEngine,
    "nback": NBackEngine,
    "dual": DualNBackEngine,
    "rotate": RotateEngine,
    "stroop": StroopEngine,
    "flanker": FlankerEngine,
    "odd": OddEngine,
    "trail": TrailEngine,
    "span": SpanEngine,
    "calc": CalcEngine,
    "category": CategoryEngine,
    "simon": SimonEngine,
    "change": ChangeEngine,
    "stop": StopEngine,
    "digits": DigitsEngine,
    "pasat": PasatEngine,
    "track": TrackEngine,
    "opspan": OspanEngine,
    "sart": SartEngine,
    "posner": PosnerEngine,
    "symdigit": SymDigitEngine,
    "dualtask": DualTaskEngine,
    "rulesearch": RuleSearchEngine,
    "rsvp": RsvpEngine,
    "antisaccade": AntisaccadeEngine,
    "running": RunningSpanEngine,
    "tower": TowerEngine,
    "conjunction": ConjunctionEngine,
    "matrix": MatrixEngine,
    "backspan": BackwardSpanEngine,
    "cpt": CptEngine,
    "partial": PartialReportEngine,
    "dichotic": DichoticEngine,
    "prospective": ProspectiveEngine,
    "loci": LociEngine,
    "countkeep": CountKeepEngine,
    "serial7": Serial7Engine,
    "cancel": CancellationEngine,
    "oddball": OddballEngine,
    "choicert": ChoiceRtEngine,
    "wordlist": WordListEngine,
    "brownpeterson": BrownPetersonEngine,
}

__all__ = [
    "ENGINES",
    "ScoreState",
    "apply_hit",
    "AdaptiveEngine",
    "DifficultyProfile",
    "build_profile",
    "clamp_level",
    "difficulty_label",
    "n_back_depth",
]
