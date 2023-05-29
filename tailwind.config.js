/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./templates/**/*.html",
      "./static/src/**/*.js",
      "./node_modules/flowbite/**/*.js"
    ],
    theme: {
        extend: {},
        colors: {
          transparent: 'transparent',
          current: 'currentColor',
          white: '#ffffff',
          blue: {
            light: '#6B4EE6',
            dark: '#0C4DCB',
          },
          pink: {
            light: '#E1DCFA',
            DEFAULT: '#BEB0F2',
            dark: '#ED6C6C',
            darkLight: '#F19090',
          },
          gray: {
            darkvar1: '#131313',
            darkvar2: '#444752',
            dark: '#333333',
            DEFAULT: '#000000',
            light: '#D9D9D9',
            lightest: '#9A9A9A',
            verylight: '#F2F8FF',
            bg: '#EEEEEE',
          }
        },
        fontFamily: {
            display: ['Prompt', 'sans-serif'],
            body: ['Lato', 'sans-serif'],
          },
      },
    plugins: [
      require("flowbite/plugin")
    ],
  }