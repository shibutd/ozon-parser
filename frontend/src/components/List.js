import React, { useContext } from 'react';
import { useParams } from 'react-router-dom';
// import PropTypes from 'prop-types';
import { ModalContext } from '../context';


export default function List() {
  // const [modal, setModal] = useContext(ModalContext);
  const { setModal } = useContext(ModalContext);
  
  const { category } = useParams();

  console.log(category);

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
    let priceString = price.toString();
    const length = priceString.length;
    if (length > 3) {
      const index = length - 3
      priceString = `${priceString.substring(0, index)} ${priceString.substring(index)}`
    }
    return `${priceString} P` 
  };

  function hadndleClick(e, item) {
    console.log(item.id);
    setModal(item.id);
  };

  return (
    <div className="relative container mx-auto w-11/12 sm:w-8/12 sm:my-8">
      <ul className="flex justify-center flex-col font-bold leading-normal tracking-wider">
          <li className="hidden sm:flex justify-between uppercase rounded-lg py-3 my-2 italic bg-red-500 text-gray-300">
          <div className="w-9/12 ml-12 text-left">
            Product Name
          </div>
          <div className="w-3/12 text-center">
            Last Price
          </div>
        </li>
        {items.map((item) => (
        <li
          key={item.id}
          className="sm:flex rounded-lg shadow-md cursor-pointer py-3 my-2 bg-gradient-to-r from-red-500 to-indigo-700 text-gray-300 transition duration-300 hover:to-red-500 hover:text-gray-100 hover:shadow-lg transform hover:scale-105"
          onClick={e => hadndleClick(e, item)}
          >
          <div className="w-9/12 text-left ml-2 sm:ml-8 truncate align-middle">
            {item.name}
          </div>
          <div className="w-6/12 sm:w-3/12 ml-2 sm:ml-8 sm:text-center">
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
