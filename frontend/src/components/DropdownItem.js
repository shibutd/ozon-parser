import React from 'react';
import PropTypes from 'prop-types';


export default function DropdownItem(props) {
  const { option, handleClick } = props;

  return (
    <a
      href={`${option.name}`}
      onClick={e => {
        e.preventDefault();
        handleClick(e, option.slug);
      }}
      className="py-2 px-4 text-md font-normal block w-full whitespace-no-wrap bg-transparent bg-white text-gray-600 transition duration-200 hover:bg-gray-600 hover:text-white"
    >
      {option.name}
    </a>
  )
}

DropdownItem.propTypes = {
  option: PropTypes.object.isRequired,
  handleClick: PropTypes.func.isRequired
}