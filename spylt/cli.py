import os

REQUIREMENTS = [
    "@rollup/plugin-commonjs",
    "@rollup/plugin-node-resolve",
    "rollup",
    "rollup-plugin-css-only",
    "rollup-plugin-livereload",
    "rollup-plugin-svelte",
    "rollup-plugin-terser",
    "svelte",
]


def pr_exists(name):
    return os.system(f"which {name}") == 0


def copy_rollup():
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "rollup.config.txt"),
        encoding="utf-8",
    ) as fh:
        with open("./rollup.config.js", "w", encoding="utf-8") as fh_:
            fh_.write(fh.read())


def template(directory):
    if os.path.exists(directory):
        raise FileExistsError(
            "Directory already exists. Choose a directory that doesn't exist yet."
        )

    os.mkdir(directory)
    os.chdir(directory)

    if not pr_exists("npm"):
        raise RuntimeError(
            "Node and NPM are not installed.\n"
            "Consider installing with NVM:\n"
            "https://github.com/nvm-sh/nvm#installing-and-updating"
        )
    os.system("npm init --y >/dev/null")
    os.system(f"npm install --save-dev {' '.join(REQUIREMENTS)} >/dev/null")
    os.system("npm install sirv-cli >/dev/null")

    if os.path.exists("./rollup.config.js"):
        inp = input(
            "You seem to have a Rollup config here already. "
            "Do you want to update it or leave it alone? (Y/n)"
        )
        if inp in ("N", "n"):
            return
    copy_rollup()
    os.mkdir("src")
    with open("src/App.svelte", "w", encoding="utf-8") as fh:
        fh.write(
            """<!-- point ./src/App.py:app -->
<script>
    export let text
    setTimeout(() => text = "Hello world!", 5000)
</script>
<main>
    <p>{text}</p>
</main>
        """
        )
    with open("src/App.py", "w", encoding="utf-8") as fh:
        fh.write(
            """from spylt import require_svelte

app = require_svelte("./src/App.svelte")
app.add_props(text="Loading...")
        """
        )

    print(
        "* Project initialized successfully! *\n"
        "Now you can setup a simple project and run: "
        "`python3 -m spylt build`"
    )
