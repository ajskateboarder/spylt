<!-- point ./src/App.py:app -->
<script>
    let text;
    import { say_hello } from "./App.py.js";
</script>

<main>
    <h2>Welcome to Spylt</h2>
    <br />
    <input type="text" name="Name" bind:value={text} />

    <p>
        {text === undefined
            ? "You're not going to say hi to anyone"
            : "You're about to say hi to  " + text}
    </p>

    <button type="submit" on:click={() => alert(say_hello(text))}>Greet</button>
</main>
