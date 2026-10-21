"""وكلاء حَكَم: المحقق، مولّدو الفرضيات، الادعاء، كبير المستشارين."""
from .analyzer import analyze
from .hypothesis import generate_all
from .synthesizer import synthesize
from .verifier import verify

__all__ = ["analyze", "generate_all", "verify", "synthesize"]
