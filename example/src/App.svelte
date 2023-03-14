<!-- point ./src/App.py:app -->
<script>
    import { say_hello } from "./App.py.js";

    let greeting
    let name = "Bob"
</script>
<main>
    <input type="text" bind:value={name}>
    <button on:click={(async function() { greeting = await say_hello(name) })()}>Say hello</button>
    <p>{greeting}</p>
</main>