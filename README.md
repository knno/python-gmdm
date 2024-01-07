# GmDm

A GameMaker Dependency Management system

## Installation

To install this project as a global Python package, you need to have Python installed on your system. Then, follow these steps:

1. Install the package using `pip install gmdm`

Otherwise, you can create a virtual environment By following these steps:

1. Create a virtual environment using `python -m venv venv`
2. Activate the virtual environment using `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install the package using `pip install gmdm`

In the second way, you will have to activate the virtual environment every time you want to use `gmdm`

## Usage

Now that you have installed this package, you can set up your projects to work with it.

For any GameMaker project to be compatible with GmDm, you will have to create a `gmdm.yml` file inside each GameMaker project's folder.
This file will define the file name, optionally imports and exports, if any, of your GameMaker projects.

It simply tells GmDm that this project imports a GameMaker "Folder" or Group of resources from other projects.
These other projects should be GmDm compatible.

### Basic Usage

To make your project GmDm compatible at least it should have this content at minimum:

##### File: C:/path/to/My Project/My Project.yyp
##### File: C:/path/to/My Project/gmdm.yml
```yml
name: My Project.yyp

```

Another example where you define a project that is to be a dependency for other projects:
```yml
name: Core.yyp
exports:
  - Sprites/My Group
  - Objects/My Group
  - Scripts/My Group
```

Now to import the project's exports:

```yml
name: Second Project.yyp
imports:
    - path/to/core
```

Basically the same as:

```yml
name: Second Project.yyp
imports:
    - path/to/core:
      - Sprites/My Group
      - Objects/My Group
      - Scripts/My Group
```

For advance usage, you can see the file `gmdm.yml.EXAMPLE`.

Now you can use `gmdm sync`, or any of these commands when inside your project directory:

```bash
gmdm sync           # performs reimporting (newely modified assets from the imported projects)
gmdm sync --fake    # displays operations without actually performing any.
gmdm sync --back    # performs sync (modified assets from and to imported projects)
```

To show the help, you can use the following command:

`gmdm --help`


## Advanced Usage

Consider using `to` in order to have the same path from multiple projects.

```yml
name: Project1.yyp
imports:
  - ../project2:
    - My Main Folder/My Folder:
      to: Extensions/My Project 2 Folder
  - ../project3:
    - My Main Folder/My Folder:
      to: Extensions/My Project 3 Folder
```

## Notes

Do:

- Keep things simple.
- Use this for your own local machine package management.
- Know what you are importing.

Do not:

- Do not import the same assets or folders that have the same assets from multiple projects.
- Do not import the same folder path from mutliple projects. Use `to` in this case.

Other:

- Zombie files are kept.
- GmDm is intelligent enough to handle renamed imports when syncing.


## Contributing

This project is open for contributions. If you want to contribute, please follow these steps:

1. Fork this repository and create a new branch
2. Make your changes and commit them with a descriptive message
3. Push your branch to your forked repository
4. Create a pull request and explain your changes

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
