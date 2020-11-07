import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';


const DropdownItem = React.memo((props) => {
  const { option } = props;
  const [isOpen, setIsOpen] = useState(false);
  const variants = {
    rotateOpen: {
      rotate: [0, 90],
      transition: { duration: 0.5 }
    },
    rotateClose: {
      rotate: [90, 0],
      transition: { duration: 0.5 }
    },
    open: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 }
    },
    closed: { opacity: 0, y: "-20%" },
  };

  return (
    <div className="cursor-pointer bg-white text-gray-600 transition duration-200 hover:bg-gray-600 hover:text-white">
      <a
        href={`${option.slug}`}
        onClick={e => {
          e.preventDefault();
          setIsOpen(!isOpen);
        }}
        className="block py-2 text-md font-semibold w-full whitespace-no-wrap"
      >
        <motion.i
          className="mx-4 my-2 fas fa-chevron-right"
          variants={variants}
          animate={isOpen ? 'rotateOpen' : 'rotateClose'}
        >
        </motion.i>
        {option.name}
      </a>
      <motion.div
        className={(isOpen ? "block" : "hidden")}
        variants={variants}
        animate={isOpen ? "open" : "closed"}
      >
        {props.children}
      </motion.div>
    </div>
  );
})

DropdownItem.propTypes = {
  option: PropTypes.object.isRequired
}

export default DropdownItem;
