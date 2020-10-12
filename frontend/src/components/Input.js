import React from 'react';
import PropTypes from 'prop-types';


export default function Input(props) {
  const { value, handleChange, error } = props;

  return (
    <>
      <input
        className="px-3 py-3 placeholder-gray-500 placeholder-opacity-50 text-gray-700 bg-white rounded tracking-wider text-md font-semibold w-full shadow-md focus:outline-none focus:shadow-outline"
        placeholder="https://ozon.ru/context/item/id/5151551/"
        type="text"
        value={value}
        onChange={handleChange}
        style={{ transition: "all .15s ease" }}
      />
      {error && (
        <div className="pt-1 w-full text-sm font-semibold text-red-500 tracking-wider">
          {error}
        </div>
      )}
    </>
  )
}

Input.propTypes = {
  value: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  error: PropTypes.string.isRequired
}