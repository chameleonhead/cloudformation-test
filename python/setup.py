import setuptools

setuptools.setup(
    name="lib",
    version="0.0.1",
    include_package_data=True,
    packages=setuptools.find_packages("site-packages"),
    package_dir={"": "site-packages"},
    package_data={
        "": ["*.*"],
    },
    data_files=[
        ("lib/python3.10/site-packages", ["site-packages/_cffi_backend.cpython-310-x86_64-linux-gnu.so"]),
    ],
)