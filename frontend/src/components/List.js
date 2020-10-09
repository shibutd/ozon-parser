import React from 'react';
// import PropTypes from 'prop-types';


export default function List(props) {

  const items = [
    {
      "id": 1,
      "name": "Notebook Samsung 15'",
      "price": 325
    },
    {
      "id": 2,
      "name": "Notebook Samsung 25'",
      "price": 33850
    },
    {
      "id": 3,
      "name": "Notebook Samsung 32'",
      "price": 45550
    },
    {
      "id": 4,
      "name": "Notebook Samsung 47'",
      "price": 75900
    },
    {
      "id": 5,
      "name": "Notebook Samsung 55'",
      "price": 85900
    }
  ];

  function convertPrice(price) {
    let strPrice = price.toString();
    const strLength = strPrice.length;
    if (strLength > 3) {
      const index = strLength - 3
      strPrice = `${strPrice.substring(0, index)} ${strPrice.substring(index)}`
    }
    return `${strPrice} P` 
  };

  function hadndleClick(e, item) {
    console.log(item);
  };

  return (
    <div className="relative container mx-auto w-8/12 py-12">
      <ul className="flex justify-center flex-col font-bold leading-normal tracking-wider">
          <li className="flex justify-between text-center rounded-lg py-3 my-2 italic bg-gradient-to-r from-red-500 to-indigo-700">
          <div class="w-3/12 ">
            Product Name
          </div>
          <div class="w-3/12">
            Last Price
          </div>
        </li>
        {items.map((item) => (
        <li
          key={item.id}
          className="flex rounded-lg shadow-md cursor-pointer py-3 my-2 bg-gradient-to-r from-red-500 to-indigo-700 transition duration-300 hover:to-red-500 hover:shadow-lg transform hover:scale-105"
          onClick={e => hadndleClick(e, item)}
          >
          <div class="w-9/12 text-left ml-8">
            {item.name}
          </div>
          <div class="w-3/12 text-center">
            {convertPrice(item.price)}
          </div>
        </li>
        ))}
      </ul>
    </div>
  )
}

// List.propTypes = {

// }
