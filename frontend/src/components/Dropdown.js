import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import DropdownItem from './DropdownItem';
import { useOnClickOutside } from '../customHooks';


export default function Dropdown(props) {
  const { options, category, changeCategory } = props;
  const [visible, setVisible] = useState(false);
  const refDropdown = useRef(null);

  useOnClickOutside(refDropdown, () => closeDropdownPopover());

  const openDropdownPopover = () => {
    setVisible(true);
  };

  const closeDropdownPopover = () => {
    setVisible(false);
  };

  const handleSelect = (e, option) => {
    changeCategory(option);
    closeDropdownPopover();
  };

  return (
    <div ref={refDropdown}>
      <button
        className="w-full font-semibold uppercase text-left px-3 py-3 mr-1 rounded shadow hover:shadow-lg outline-none focus:outline-none bg-white text-gray-600"
        style={{ transition: "all .15s ease" }}
        type="button"
        onClick={() => {
          visible
            ? closeDropdownPopover()
            : openDropdownPopover();
        }}
      >
        {!category ? 'Select...' : category}
      </button>
      <div
        className={
          (visible ? "block " : "hidden ") +
          "absolute w-11/12 mt-2 text-base z-50 float-left list-none text-left rounded shadow-lg"
        }
      >
      
      {options.status === 'loading' && (
        <div
          className="py-2 px-4 text-md font-normal block w-full whitespace-no-wrap bg-white text-gray-600"
        >
        Loading...
        </div>
      )}

      {options.status === 'error' && (
        <div
          className="py-2 px-4 text-md font-normal block w-full whitespace-no-wrap bg-white text-gray-600"
        >
        Error retreiving categories. Please try again later
        </div>
      )}

      {options.status === 'success' && (
        <div>
          {options.data.map(option => (
            <DropdownItem
              key={option.slug}
              option={option}
              handleClick={handleSelect}
            />
          ))}
        </div>
      )}

      </div>
    </div>
  );
}

Dropdown.propTypes = {
  options: PropTypes.object.isRequired,
  category: PropTypes.string.isRequired,
  changeCategory: PropTypes.func.isRequired,
}