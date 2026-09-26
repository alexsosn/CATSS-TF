def test_package_exposes_version() -> None:
    import catss_tf

    assert catss_tf.__version__ == "0.1.0"
