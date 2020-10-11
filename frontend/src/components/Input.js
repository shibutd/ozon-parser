import React from 'react';


export default function Input(props) {
  const { value, changeValue } = props;

  function handleChange(e) {
    changeValue(e.target.value);
  };

  return (
    <div>
      <input
        className="px-3 py-3 placeholder-gray-500 placeholder-opacity-50 text-black bg-white rounded tracking-wider text-md w-full shadow-md focus:outline-none focus:shadow-outline"
        placeholder="https://ozon.ru/context/item/id/5151551/"
        type="text"
        value={value}
        onChange={handleChange}
        style={{ transition: "all .15s ease" }}
      />
    </div>
  )
}