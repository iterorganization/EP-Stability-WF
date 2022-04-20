import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EP-Stability-WF",
    version="1.0.0",
    author="Alin Popa, Thomas Hayward-Schneider, Philipp Lauber",
    author_email="alin.popa@ipp.mpg.de",
    description="Energetic Particle workflow for stability analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://confluence.iter.org/pages/viewpage.action?pageId=289069024",
    packages=setuptools.find_packages(),
    package_data = {"": ["*.xml"]},
    scripts=[
        'ep_gui',
        'ep_nogui',
    ],
    include_package_data = True,
    python_requires='>=3.6',
)
