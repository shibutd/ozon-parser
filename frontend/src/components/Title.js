import React from 'react';
import { motion } from 'framer-motion';


export default function Title({ text }) {
  const title = Array.from(text);

  return (
    <>
      {title.map((letter, i) => (
        <motion.div
          key={i}
          className="text-gray-100 font-title uppercase text-6xl sm:text-8xl"
          variants={{
            'visible': (i) => ({
              y: 0, 
              opacity: 1,
              transition: { delay: i * 0.03 }
          }),
            'hidden': { y: 150, opacity: 0 }
          }}
          animate='visible'
          initial='hidden'
          custom={i}
        >
          {letter}
        </motion.div>
      ))}
    </>
  )
}