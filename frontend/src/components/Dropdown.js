import React, { useState, useRef } from 'react';
import { useOnClickOutside } from '../customHooks';


export default function Dropdown() {
  const [visible, setVisible] = useState(false);
  const refDropdown = useRef(null);

  useOnClickOutside(refDropdown, () => closeDropdownPopover());

  const options = [
    {
      "id": 1,
      "name": "first"
    },
    {
      "id": 2,
      "name": "second"
    },
    {
      "id": 3,
      "name": "third"
    }
  ];

  const openDropdownPopover = () => {
    setVisible(true);
  };
  const closeDropdownPopover = () => {
    setVisible(false);
  };

  const setOptionName = (e, option) => {
    e.preventDefault();
    console.log(option.name);
    closeDropdownPopover();
  };

  return (
    <>
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
          Choose...
        </button>
        <div
          className={
            (visible ? "block " : "hidden ") +
            "absolute w-11/12 mt-2 text-base z-50 float-left list-none text-left rounded shadow-lg"
          }
        >
        {options.map((option) => (
          <a
            key={option.id}
            href={`#${option.name}`}
            className="py-2 px-4 text-md font-normal block w-full whitespace-no-wrap bg-transparent bg-white text-gray-600 transition duration-200 hover:bg-gray-600 hover:text-white"
            onClick={e => setOptionName(e, option)}
          >
            {option.name}
          </a>
        ))}
        </div>
      </div>
    </>
  );
}
