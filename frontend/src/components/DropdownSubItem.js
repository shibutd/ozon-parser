import React from 'react';
import PropTypes from 'prop-types';


export default function DropdownSubItem(props) {
  const { option, handleClick } = props;

  return (
    <div
      className="flex items-center cursor-pointer bg-white text-gray-600 transition duration-200 hover:bg-gray-600 hover:text-white"
    >
      <a
        href={`${option.slug}`}
        onClick={e => {
          e.preventDefault();
          handleClick(e, option);
        }}
        className="py-2 ml-6 text-md font-semibold w-full whitespace-no-wrap"
      >
        {option.name}
      </a>
    </div>
  );
}

DropdownSubItem.propTypes = {
  option: PropTypes.object.isRequired,
  handleClick: PropTypes.func.isRequired
}
