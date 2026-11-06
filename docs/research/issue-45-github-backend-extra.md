# Research — issue #45 GitHub parent backend dependency

## Reproducer

The documented clean install is `catss-tf[tf]`, followed by
`tf.app.use("ETCBC/bhsa:v1.8.1", ...)` or `tf.app.use("CenterBLC/LXX:v1.0.1", ...)`.
Current `pyproject.toml` declares `tf = ["text-fabric>=13.1,<14"]`.

On a fresh Ubuntu/Python 3.11 environment, Text-Fabric 13.1 reports that the
GitHub backend provider is unsupported and recommends
`pip install text-fabric[github]`. Reproducer: #41/#42 release-style smoke
run 36242652802.

## Upstream dependency evidence

Text-Fabric's own `tf/capable.py` documents that its optional backend
`github` requires Python module `github`, supplied by `pygithub`.
The upstream `setup.cfg` declares:

```
[options.extras_require]
github = pygithub>=1.57
gitlab = python-gitlab>=3.5.0
all = pygithub>=1.57; python-gitlab>=3.5.0
```

Thus the smallest correct dependency is
`text-fabric[github]>=13.1,<14`. Adding `text-fabric[all]` would
unnecessarily install an independent GitLab integration.

## Acceptance constraints

- `tf` and developer extras must use the same Github-capable TF requirement;
- a clean wheel installation must resolve `PyGithub` transitively;
- smoke must verify `github` import and `tf.capable.Capable("github")`
  without downloading either large parent corpus in normal CI;
- normal package import without extras remains minimal;
- pinned BHSA and LXX corpus identities do not change.
