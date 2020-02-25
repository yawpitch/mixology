from mixology.failure import SolverFailure
from mixology.package import Package
from mixology.version_solver import VersionSolver


def check_solver_result(source, result=None, error=None, tries=None):
    solver = VersionSolver(source)

    try:
        solution = solver.solve()
    except SolverFailure as e:
        if error:
            assert str(e) == error

            if tries is not None:
                assert solver.solution.attempted_solutions == tries

            return None

        raise

    packages = {}
    for package, version in solution.decisions.items():
        if package == Package.root():
            continue

        packages[package] = str(version)

    assert result == packages

    if tries is not None:
        assert solution.attempted_solutions == tries
