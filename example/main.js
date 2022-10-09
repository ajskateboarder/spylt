import App from './App.svelte';

const app = new App({
    target: document.body,
    props: {
      text: "Pooping...",
      age: "Pooping..."
    }
});

export default app;