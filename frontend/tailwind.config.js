module.exports = {
  purge: {
    content: [
      './src/*.js',
      './src/*.jsx'
    ],
    options: {
      whitelist: ['bg-color-500']
    }
  },  
  theme: {
    extend: {
      maxWidth: {
        '20': '20%',
        '40': '40%',
        '60': '60%',
        '80': '80%',
      },
      maxHeight: {
        '20': '20%',
        '40': '40%',
        '60': '60%',
        '80': '80%',
      },
      fontFamily: {
        title: ['Kaushan Script'],
      },
      fontSize: {
        '8xl': '6rem',
      },
      scale: {
        '102': '1.02',
      },
      height: {
        '72': '18rem',
        '80': '20rem',
      }
    }
  }
}
