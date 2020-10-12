import React, { useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { usePaginatedQuery } from 'react-query';
import axios, { CancelToken } from 'axios';
import { ModalContext } from '../context';
import { getItemsUrl } from '../constants';


async function fetchItems(key, page, category) {
  const source = CancelToken.source()

  const promise = await axios.get(
    `${getItemsUrl}?category=${category}&page=${page}`,
    {
      cancelToken: source.token,
    }
  );

  promise.cancel = () => {
    source.cancel('Query was cancelled')
  };
 
  return promise.data;
} 

export default function List() {
  const { setModal } = useContext(ModalContext);
  const [page, setPage] = useState(1);
  const { category } = useParams();
  const { 
    resolvedData,
    latestData,
    status
  } = usePaginatedQuery(['items', page, category], fetchItems, {
    staleTime: 6000,
    cachedTime: 60000,
    refetchOnWindowFocus: false,
  });

  // function convertPrice(price) {
  //   let priceString = price.toString();
  //   const length = priceString.length;
  //   if (length > 3) {
  //     const index = length - 3
  //     priceString = `${priceString.substring(0, index)} ${priceString.substring(index)}`
  //   }
  //   return `${priceString} P` 
  // };
  
  function decreasePage() {
    setPage(old => Math.max(old - 1, 1));
  };

  function increasePage() {
    setPage(old => (!latestData || !latestData.next ? old : old + 1));
  };

  function hadndleClick(e, item) {
    setModal(item.id);
  };

  if (status === 'loading') {
    return (
      <div className="text-4xl font-bold text-white text-center">
        Loading...
      </div>
    );
  };

  if (status === 'error') {
    return (
      <div className="text-4xl font-bold text-white text-center">
        Something went wrong... Please try again
      </div>
    );
  };

  if (status === 'success') {
    return (
      <div className="relative container mx-auto w-11/12 sm:w-8/12 sm:my-8">
        <ul className="flex justify-center flex-col font-bold leading-normal tracking-wider">
          <li className="hidden sm:flex justify-between uppercase rounded-lg py-3 my-2 italic bg-red-500 text-gray-300 shadow-md">
            <div className="w-9/12 ml-12 text-left">
              Product Name
            </div>
            {/*<div className="w-3/12 text-center">
              Last Price
            </div>*/}
          </li>
          {resolvedData.results.map(item => (
          <li
            key={item.id}
            className="sm:flex rounded-lg shadow-md cursor-pointer py-3 my-2 bg-gradient-to-r from-red-500 to-indigo-700 text-gray-300 transition duration-300 hover:to-red-500 hover:text-gray-100 hover:shadow-lg transform hover:scale-105"
            onClick={e => hadndleClick(e, item)}
          >
            <div className="w-9/12 text-left ml-2 sm:ml-8 truncate align-middle">
              {item.name}
            </div>
            {/*<div className="w-6/12 sm:w-3/12 ml-2 sm:ml-8 sm:text-center">
              {convertPrice(item.price)}
            </div>*/}
          </li>
          ))}
        </ul>
        <div className="flex justify-end w-full pt-2 pr-2 text-gray-300">
          <button 
            onClick={decreasePage}
            className="mr-2 bg-red-500 rounded-full h-12 w-12 flex items-center justify-center shadow-md focus:outline-none transition duration-300 hover:shadow-lg transform hover:scale-105">
            <i className="fas fa-chevron-left"></i>
          </button>
          <button 
            onClick={increasePage}
            className="bg-red-500 rounded-full h-12 w-12 flex items-center justify-center shadow-md focus:outline-none transition duration-300 hover:shadow-lg transform hover:scale-105">
            <i className="fas fa-chevron-right"></i>
          </button>

        </div>
      </div>
    );
  };
}
