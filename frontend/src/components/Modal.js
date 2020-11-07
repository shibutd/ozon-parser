import React, { useContext, useRef } from 'react';
import { useQuery } from 'react-query';
import axios, { CancelToken } from 'axios';
import { motion } from 'framer-motion';
import LineChart from './LineChart';
import { ModalContext } from '../context';
import { useOnClickOutside } from '../customHooks';
import { getItemsUrl } from '../constants';


async function fetchItem(key, modal) {
  const source = CancelToken.source()

  const promise = await axios.get(`${getItemsUrl}/${modal}`, {
    cancelToken: source.token,
  });

  promise.cancel = () => {
    source.cancel('Query was cancelled')
  };

  return promise.data;
}

export default function Modal() {
  const { modal, setModal } = useContext(ModalContext);
  const refModal = useRef(null);
  const { data, status } = useQuery(['categories', modal],
    fetchItem,
    {
      staleTime: 6000,
      cachedTime: 60000,
      refetchOnWindowFocus: false,
    }
  );

  useOnClickOutside(refModal, () => setModal(null));

  function getLastItemPrice(prices) {
    const lastPrice = prices[prices.length - 1];
    return `${lastPrice.value} P`;
  };

  if (status === 'error') {
    return (
      <div
        className="z-50 fixed top-0 left-0 w-full h-full pt-16 bg-gray-700 bg-opacity-75"
      >
        <div ref={refModal} className="relative container mx-auto flex  flex-col w-9/12 h-auto rounded-lg shadow-lg bg-gray-200 py-16">
          <div className="text-gray-700 font-semibold text-4xl text-center">Something wrong here!
          </div>
          <div className="m-4 text-gray-700 font-semibold text-md text-center">
            Sorry, the item you were looking for could not be found...
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      className="z-50 fixed top-0 left-0 w-full h-full pt-16 bg-gray-700 bg-opacity-75"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.7 }}
    >
      <div ref={refModal} className="relative container mx-auto flex  flex-col md:flex-row w-9/12 h-auto rounded-lg shadow-lg bg-gray-200 pt-4 md:pt-0">

        <div className="flex justify-center w-4/12 mx-auto my-auto">
          {status === 'loading' && (
            <div className="h-40 md:h-64 w-32 md:w-48 shadow-lg rounded-lg border-none bg-gray-400 pb-4 animate-pulse"
            />
          )}
          {status === 'success' && (
            <div className="bg-gray-100 text-black border-none shadow-lg rounded-lg">
              <img
                alt="product"
                src={data.image_url}
                className="min-wd-full border-none py-2 px-2"
              />
            </div>
          )}
        </div>

        <div className="flex flex-col w-full md:w-8/12 rounded-lg px-2">
          {status === 'loading' && (
            <div className="flex flex-col w-full w-full my-2 pr-4 animate-pulse">
              <div className="w-full h-16 bg-gray-400 ml-2 my-2" />
              <div className="w-8/12 h-12 bg-gray-400 ml-2 my-2" />
              <div className="w-full h-40 md:h-80 bg-gray-400 ml-2 my-2" />
            </div>
          )}
          {status === 'success' && (
            <>
              <div className="text-3xl font-semibold leading-none text-gray-700 pl-4 md:pl-2 py-4">
                {data.name}
              </div>
              <div className="text-lg uppercase font-bold tracking-wide text-red-600 pl-4 md:pl-2 py-2">
                Last Price: {getLastItemPrice(data.prices)}
              </div>
              <div className="pt-2 pb-2 md:pt-4">
                <LineChart data={data.prices} />
              </div>
            </>
          )}
        </div>

      </div>
    </motion.div>
  )
}