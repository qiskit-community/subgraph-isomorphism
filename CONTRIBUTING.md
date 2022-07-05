# Contributing

**We appreciate all kinds of help, so thank you!**

## Code contribution guide
This guide is for those who want to extend the module or documentation. If you just want to use 
the package, take a look at the [demo](./docs/subgraph-isomorphism-demo.ipynb) instead.

Code in this repository should conform to PEP8 standards. Style/lint checks are run to validate 
this. Line length must be limited to no more than 100 characters.

### Initial set-up and installing dependencies
In order to contribute, you will need to install the module from source. 
If you do not have write permissions to the original Subgraph Isomorphism repo, you will need to 
fork it to your personal account first, and submit all Pull Requests (PR) from there. Even if you 
have write permissions, forking the repo should always work, so this is the recommended approach.

### Installing from sources
0. Make sure you have [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) 
and [pip](https://pip.pypa.io/en/stable/installation/) (and optionally
[Miniconda](https://docs.conda.io/en/latest/miniconda.html)) installed.

1. From the terminal, clone repository:
    ```
    git clone https://github.com/qiskit-community/subgraph-isomorphism.git
    ```
    Alternatively, instead of cloning the original repository, you may choose to clone your 
    personal [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo). You can do so 
    by using the appropriate URL and adding the original repo to the list of remotes (here under 
    the name `upstream`). This will be required for contribution unless you are granted write 
    permissions for the original repository.
    ```
    git clone <YOUR-FORK-URL>
    git remote add upstream https://github.com/qiskit-community/subgraph-isomorphism.git
    ```
2. Change directory to the freshly cloned subgraph isomorphism module:
    ```
    cd subgraph-isomorphism
    ```
3. Install the dependencies needed:
    ```
    pip install .
    ```
4. (Optional) Install the repo in editable mode and with developer dependencies for contributing:
    ```
    pip install -e .[dev]
    ```

### Making a pull request

#### Step-by-step
1. To make a contribution, first set up a remote branch (here called `my-contribution`) either 
in your fork (i.e. `origin`) or the original repo (i.e. `upstream`). In the absence of a fork, 
the (only) remote will simply be referred to all the time by the name `origin` (i.e. replace 
`upstream` in all commands):

   ```
   git checkout main
   git pull origin
   git checkout -b my-contribution
   ```
   ... make your contribution now (edit some code, add some files) ...
   ```
   git add .
   git commit -m 'initial working version of my contribution'
   git push -u origin my-contribution
   ```
2. Before making a Pull Request always get the latest changes from `main` (`upstream` if there is 
a fork, `origin` otherwise):
   ```
   git checkout main
   git pull upstream
   git checkout my-contribution
   git merge main
   ```
   ... fix any merge conflicts here ...
   ```
   git add .
   git commit -m 'merged updates from main'
   git push
   ```
3. Go back to the appropriate Subgraph Isomorphism repo on GitHub (i.e. fork or original), switch 
to your contribution branch (same name: `my-contribution`), and click _"Pull Request"_. Write a 
clear explanation of the feature.
4. Under _Reviewer_, select Nicola Mariella __and__ Anton Dekusar.
5. Click _"Create Pull Request"_.
6. Your Pull Request will be reviewed and, if everything is ok, it will be merged.

#### Pull request checklist
When submitting a pull request and you feel it is ready for review, please ensure that the code 
follows the _code style_ of this project.

Subgraph Isomorphism uses [Pylint](https://www.pylint.org), [Black](https://github.com/psf/black) 
and [PEP8](https://www.python.org/dev/peps/pep-0008) style guidelines. For this you can run:
   ```
   black qsubgisom
   ```
and
   ```
   pylint -rn qsubgisom
   ```


## Other ways of contributing
Other than submitting new source code, users can contribute in the following meaningful ways:
 - __Reporting Bugs and Requesting Features__: Users are encouraged to use Github Issues for 
reporting issues are requesting features.
 - __Ask/Answer Questions and Discuss Subgraph Isomorphism__: Users are encouraged to use Github 
Discussions for engaging with researchers, developers, and other users regarding this project.