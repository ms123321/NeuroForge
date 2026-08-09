"""Training modes targeting distinct cognitive domains.

MODE_META is always available (web-safe, no tkinter).
MODES (tkinter UI classes) load only when Tk is available (desktop).
"""

from __future__ import annotations

from .meta import MODE_META

# Desktop UI mode classes — require tkinter (not on Render/Linux servers)
MODES: dict = {}

try:
    from .focus import FocusPulse
    from .memory import MemoryLattice
    from .switch import SwitchPath
    from .speed import SpeedMirror
    from .nback import NBackLite
    from .dual import DualNBack
    from .rotate import MentalRotate
    from .stroop import StroopClash
    from .flanker import FlankerForce
    from .odd import OddSpot
    from .trail import NumberPath
    from .span import BlockSpan
    from .calc import QuickCalc
    from .category import CategoryFlex
    from .simon import SimonClash
    from .change import ChangeDetect
    from .stop import StopSignal
    from .digits import DigitSpan
    from .pasat import PasatLite
    from .track import ObjectTrack
    from .opspan import OpSpan
    from .sart import SartMode
    from .posner import PosnerMode
    from .symdigit import SymDigitMode
    from .dualtask import DualTaskMode
    from .rulesearch import RuleSearchMode
    from .rsvp import RsvpMode
    from .antisaccade import AntisaccadeMode
    from .running import RunningSpanMode
    from .tower import TowerMode
    from .conjunction import ConjunctionMode
    from .matrix import MatrixMode
    from .backspan import BackSpanMode
    from .cpt import CptMode
    from .partial import PartialMode
    from .dichotic import DichoticMode
    from .prospective import ProspectiveMode
    from .loci import LociMode
    from .countkeep import CountKeepMode
    from .serial7 import Serial7Mode
    from .cancel import CancelMode
    from .oddball import OddballMode
    from .choicert import ChoiceRtMode
    from .wordlist import WordListMode
    from .brownpeterson import BrownPetersonMode

    MODES = {
        "focus": FocusPulse,
        "memory": MemoryLattice,
        "switch": SwitchPath,
        "speed": SpeedMirror,
        "nback": NBackLite,
        "dual": DualNBack,
        "rotate": MentalRotate,
        "stroop": StroopClash,
        "flanker": FlankerForce,
        "odd": OddSpot,
        "trail": NumberPath,
        "span": BlockSpan,
        "calc": QuickCalc,
        "category": CategoryFlex,
        "simon": SimonClash,
        "change": ChangeDetect,
        "stop": StopSignal,
        "digits": DigitSpan,
        "pasat": PasatLite,
        "track": ObjectTrack,
        "opspan": OpSpan,
        "sart": SartMode,
        "posner": PosnerMode,
        "symdigit": SymDigitMode,
        "dualtask": DualTaskMode,
        "rulesearch": RuleSearchMode,
        "rsvp": RsvpMode,
        "antisaccade": AntisaccadeMode,
        "running": RunningSpanMode,
        "tower": TowerMode,
        "conjunction": ConjunctionMode,
        "matrix": MatrixMode,
        "backspan": BackSpanMode,
        "cpt": CptMode,
        "partial": PartialMode,
        "dichotic": DichoticMode,
        "prospective": ProspectiveMode,
        "loci": LociMode,
        "countkeep": CountKeepMode,
        "serial7": Serial7Mode,
        "cancel": CancelMode,
        "oddball": OddballMode,
        "choicert": ChoiceRtMode,
        "wordlist": WordListMode,
        "brownpeterson": BrownPetersonMode,
    }
except ImportError:
    # Server / web (no _tkinter): engines still run via neuroforge.logic
    MODES = {}

__all__ = ["MODE_META", "MODES"]
