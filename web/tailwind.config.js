/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                lattice: {
                    bg: '#0a0a0a',
                    panel: '#1a1a1a',
                    border: '#333333',
                    primary: '#00ff9d',
                    accent: '#00e5ff',
                    alert: '#ff3333',
                    warning: '#ffae00',
                }
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
            }
        },
    },
    plugins: [],
}
