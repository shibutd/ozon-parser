import React from 'react';
import { motion } from 'framer-motion';

export default function Title({ text }) {
  const title = Array.from(text);
  const fullWord = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        delayChildren: 0.7,
        staggerChildren: 0.15,
        staggerDirection: 1
      }
    }
  };
  const letterWord = {
    hidden: { opacity: 0 },
    show: { opacity: 1 }
  };

  return (
    <motion.div>
      <motion.span variants={fullWord} initial='hidden' animate='show'>
      {title.map((letter, index) => (
        <motion.span
          key={index}
          variants={letterWord}
          size={50}
          className="text-gray-100 font-title uppercase text-6xl sm:text-8xl"
        >
          {letter}
        </motion.span>
      ))}
      </motion.span>
    </motion.div>
  )
}
