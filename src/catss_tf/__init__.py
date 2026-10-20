"""Public CATSS-TF v0.1 API."""

__version__ = "0.1.0"

from catss_tf.bhsa_materializer import materialize_bhsa
from catss_tf.bhsa_resolver import TextFabricBhsaProvider
from catss_tf.canonical_materializer import materialize_corpus
from catss_tf.consistency import (
    compare_canonical_projection_bundle,
    compare_projection_bundles,
)
from catss_tf.lxx_materializer import materialize_lxx
from catss_tf.lxx_resolver import TextFabricLxxProvider
from catss_tf.query import (
    AlignmentAnnotationEvidence,
    CanonicalAlignedGroup,
    SirachWitnessAnnotation,
    UnclassifiedAlignment,
    find_aligned_groups,
    find_sirach_witness_annotations,
    find_unclassified_alignments,
)

__all__ = [
    "__version__",
    "compare_canonical_projection_bundle",
    "compare_projection_bundles",
    "AlignmentAnnotationEvidence",
    "CanonicalAlignedGroup",
    "SirachWitnessAnnotation",
    "UnclassifiedAlignment",
    "find_aligned_groups",
    "find_sirach_witness_annotations",
    "find_unclassified_alignments",
    "materialize_bhsa",
    "materialize_corpus",
    "materialize_lxx",
    "TextFabricBhsaProvider",
    "TextFabricLxxProvider",
]
