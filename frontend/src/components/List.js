import React, { useState, useContext, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { usePaginatedQuery } from 'react-query';
import axios, { CancelToken } from 'axios';
import { motion, AnimatePresence } from "framer-motion"
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
  const refRightButtonClicked = useRef(false);
  const refLeftButtonClicked = useRef(false);
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

  const variants = {
    hiddenFromLeft: (i) => ({ x: -50 * i, opacity: 0 }),
    hiddenFromRight: (i) => ({ x: 50 * i, opacity: 0 }),
    visible: (i) => ({
      x: 0,
      opacity: 1,
      transition: { delay: i * 0.025, duration: 0.3 }
    }),
    removedToRight: { x: 100, opacity: 0 },
    removedToLeft: { x: -100, opacity: 0}
  };

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
    refRightButtonClicked.current = false;
    refLeftButtonClicked.current = true;
    setPage(old => Math.max(old - 1, 1));
  };

  function increasePage() {
    refLeftButtonClicked.current = false;
    refRightButtonClicked.current = true;
    setPage(old => (!latestData || !latestData.next ? old : old + 1));
  };

  function hadndleClick(e, item) {
    setModal(item.id);
  };

  if (status === 'loading') {
    return (
      <div className="text-4xl font-bold text-white text-center pt-16">
        Loading...
      </div>
    );
  };

  if (status === 'error') {
    return (
      <div className="text-4xl font-bold text-white text-center pt-16">
        Something went wrong... Please try again
      </div>
    );
  };

  if (status === 'success') {
    return (
      <div className="relative container mx-auto w-11/12 sm:w-8/12 sm:my-8">
        {resolvedData.results.length > 0 ? (
        <>
        <ul
          className="flex justify-center flex-col font-bold leading-normal tracking-wider"
        >
          <motion.li
            className="hidden sm:flex justify-between uppercase font-title rounded-lg py-3 my-2 italic bg-red-500 text-gray-300 shadow-md"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
            <div className="w-9/12 ml-12 text-left">
              Product Name
            </div>
            {/*<div className="w-3/12 text-center">
              Last Price
            </div>*/}
          </motion.li>
        <AnimatePresence exitBeforeEnter>
          <motion.div>
            {resolvedData.results.map((item, i) => (
              <motion.div
                key={item.id}
                className="sm:flex rounded-lg shadow-md cursor-pointer py-3 my-2 bg-gradient-to-r from-red-500 to-indigo-700 text-gray-300 transition duration-300 hover:to-red-500 hover:text-gray-100 hover:shadow-lg"
                onClick={e => hadndleClick(e, item)}
                variants={variants}
                animate='visible'
                initial={
                  refRightButtonClicked.current
                    ? 'hiddenFromLeft'
                    : 'hiddenFromRight'
                }
                exit={
                  refRightButtonClicked.current
                    ? 'removedToLeft'
                    : 'removedToRight'
                }
                custom={i}
                whileHover={{ scale: 1.05 }}
              >
                <div className="w-9/12 text-left ml-2 sm:ml-8 truncate align-middle">
                  {item.name}
                </div>
                {/*<div className="w-6/12 sm:w-3/12 ml-2 sm:ml-8 sm:text-center">
                  {convertPrice(item.price)}
                </div>*/}
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>
        </ul>

        <div className="flex justify-end w-full pt-2 pr-2 text-gray-300">
          <motion.button
            onClick={decreasePage}
            className="mr-2 bg-red-500 rounded-full h-12 w-12 flex items-center justify-center shadow-md focus:outline-none transition duration-200 hover:shadow-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.7 }}
          >
            <i className="fas fa-chevron-left"></i>
          </motion.button>
          <motion.button
            onClick={increasePage}
            className="bg-red-500 rounded-full h-12 w-12 flex items-center justify-center shadow-md focus:outline-none transition duration-200 hover:shadow-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.7 }}
          >
            <i className="fas fa-chevron-right"></i>
          </motion.button>

        </div>
        </>)
        : (
          <div className="text-4xl font-bold text-white text-center pt-16">
            No items in this category yet...
          </div>
        )}
      </div>

    );
  };
}
