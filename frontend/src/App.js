import React, { useContext } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom';
import { motion } from 'framer-motion';
import Title from './components/Title';
import Form from './components/Form';
import List from './components/List';
import Modal from './components/Modal';
import InfoTab from './components/InfoTab';
import { ModalContext } from './context';


export default function App() {
  const { modal } = useContext(ModalContext);

  return (
    <Router>
      <main>
        <div className="relative pt-8 pb-32 bg-indigo-600 overflow-x-hidden"
            style={{
              minHeight: "84vh"
            }}>
          <div className="container relative mx-auto">
            <a
              href="/"
              className="flex justify-center items-center flex-wrap overflow-hidden px-4 pb-10 m-auto"
            >
              <div className="flex md:mr-8">
                <Title text={'Ozon'}/>
              </div>
              <div className="flex">
                <Title text={'Parser'}/>
              </div>
            </a>

            {/* Switch section */}
            <Switch>
              <Route exact path="/">
                <Form />
                { modal && <Modal /> }
              </Route>
              <Route path="/categories/:category">
                <List />
                { modal && <Modal /> }
              </Route>
              <Route path="*">
                <div className="text-gray-100 font-semibold text-4xl text-center">This page does not exists!
                </div>
                <div className="text-gray-100 font-semibold text-md text-center">
                  Sorry, the page you were looking for could not be found...
                </div>
              </Route>
            </Switch>
            {/* Switch section End */}

          </div>
          <div
            className="top-auto bottom-0 left-0 right-0 w-full absolute pointer-events-none overflow-hidden"
            style={{ height: "70px", transform: "translateZ(0)" }}
          >
            <svg
              className="absolute bottom-0 overflow-hidden"
              preserveAspectRatio="none"
              xmlns="http://www.w3.org/2000/svg"
              version="1.1"
              viewBox="0 0 2560 100"
              x="0"
              y="0"
            >
              <polygon
                className="text-red-500 fill-current"
                points="2560 0 2560 100 0 100"
              ></polygon>
            </svg>
          </div>
        </div>

        {/* Infotabs section */}
        <section className="pb-10 md:pb-20 bg-red-500 -mt-24">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap z-10">
              <motion.div
                className="lg:pt-12 pt-6 w-full md:w-4/12 px-4 text-center"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.95 }}
              >
                <InfoTab
                  color="bg-red-400"
                  icon="fas fa-search"
                  title="Easy Search"
                  msg="Search products by site URL, ID or Category"
                />
              </motion.div>
              <motion.div
                className="w-full md:w-4/12 px-4 text-center"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.95 }}
              >
                <InfoTab
                  color="bg-blue-400"
                  icon="fas fa-chart-line"
                  title="Price Charts"
                  msg="Price history over last several months"
                />
              </motion.div>
              <motion.div
                className="md:pt-6 px-4 w-full md:w-4/12 text-center"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.95 }}
              >
                <InfoTab
                  color="bg-red-400"
                  icon="far fa-envelope-open"
                  title="Subscribe"
                  msg="Subscribe to receive notifications!"
                />
              </motion.div>
            </div>
          </div>
        </section>
        {/* Infotabs section End */}

      </main>
    </Router>
  );
}
