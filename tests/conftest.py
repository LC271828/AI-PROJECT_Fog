import inspect
import logging
import pytest


# Attach test phase reports to the item so our fixture can print the result
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def _announce_test(request):
    """Autouse fixture that logs a compact banner for each test.

    It prints the nodeid and the test function's docstring (if any) at start,
    then prints the final outcome and duration at the end. Works nicely with
    log_cli=true so messages appear live during the run.
    """
    logger = logging.getLogger("tests")
    item = request.node
    func = getattr(item, "function", None)
    doc = inspect.getdoc(func) if func else None

    # Start banner
    logger.info("▶ %s%s", item.nodeid, f" — {doc}" if doc else "")

    yield

    # End banner with outcome/duration
    rep = getattr(item, "rep_call", None)
    if rep is not None:
        logger.info("✓ %s — %s in %.3fs", item.nodeid, rep.outcome.upper(), rep.duration)
    else:
        # setup/teardown/skip only
        rep_setup = getattr(item, "rep_setup", None)
        if rep_setup and rep_setup.skipped:
            logger.info("○ %s — SKIPPED", item.nodeid)
        else:
            logger.info("○ %s — NO CALL PHASE", item.nodeid)
