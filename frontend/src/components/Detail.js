import React, { useState, useEffect, useContext, useRef } from 'react';
import LineChart from './LineChart';
import { ModalContext } from '../context';
import { useOnClickOutside } from '../customHooks';


export default function Detail() {
  const { setModal } = useContext(ModalContext);

  const refModal = useRef(null);

  useOnClickOutside(refModal, () => setModal(null));

  const item = {
    "name": "Samsung LED 17 inch",
    "externalUrl": "/context/detail/id/193991548/",
    "imageURL": "",
    "prices": [
      {"value": 23, "date": "2020-05-26"},
      {"value": 22, "date": "2020-05-27"},
      {"value": 21, "date": "2020-05-28"},
      {"value": 25, "date": "2020-05-29"},
      {"value": 20, "date": "2020-05-30"},
      {"value": 18, "date": "2020-05-31"}

    ]
  };

  function getLastItemPrice(prices) {
    const lastPrice = prices[prices.length - 1];
    return `${lastPrice.value} P`;
  };

  // function handleClick(e) {
  //   if (e.target.classList.contains('back')) {
  //     setModal(null);
  //   }
  // }

  // useEffect(() => {
    // fetch
  // }, []);

  return (
    <div className="z-50 fixed top-0 left-0 bg-gray-700 bg-opacity-75 w-full h-full pt-16">
      <div ref={refModal} className="relative container mx-auto block flex flex-col md:flex-row w-9/12 px-1 sm:px-12 py-4 sm:py-8 rounded-lg bg-gray-100">
        <div className="flex self-center justify-center w-4/12">
          <img
            alt="product"
            src={"https://cdn1.ozone.ru/s3/multimedia-m/wc250/6022191070.jpg"}
            className="px-3 py-3 w-32 md:w-48 shadow-lg rounded justify-center align-middle border-none"
            style={{ maxWidth: 300 }}
          />
        </div>
        <div className="flex flex-col w-full md:w-8/12 my-4">
          <div className="text-3xl font-semibold leading-none text-gray-700  ml-2 mb-2">
            {item.name}
          </div>
          <div className="text-base uppercase font-bold tracking-wide text-red-600 ml-2 mb-2">
            Last Price: {getLastItemPrice(item.prices)}
          </div>
          <LineChart data={item.prices} />
        </div>
      </div>
    </div>
  )
}