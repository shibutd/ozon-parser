import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';


const DropdownSubItem = React.memo((props) => {
  const { option, handleClick } = props;
  const variants = {
    opened: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.4, type: "tween" }
    },
    closed: { opacity: 0, x: "-20%" },
  };

  return (
    <div
      className="flex items-center cursor-pointer bg-white text-gray-600 transition duration-200 hover:bg-gray-600 hover:text-white"
    >
      <motion.a
        href={`${option.slug}`}
        onClick={e => {
          e.preventDefault();
          handleClick(e, option);
        }}
        className="py-2 ml-6 text-md font-semibold w-full whitespace-no-wrap"
        variants={variants}
        initial='closed'
        animate='opened'
      >
        {option.name}
      </motion.a>
    </div>
  );
})

DropdownSubItem.propTypes = {
  option: PropTypes.object.isRequired,
  handleClick: PropTypes.func.isRequired
}

export default DropdownSubItem;
