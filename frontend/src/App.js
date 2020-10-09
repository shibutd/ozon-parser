import React from "react";
import Form from './components/Form';
import List from './components/List';
import Detail from './components/Detail';
import InfoTab from './components/InfoTab';

export default function App() {
  return (
    <>
      <main>
        <div className="relative pt-8 pb-32 bg-indigo-600"
            style={{
              minHeight: "72vh"
            }}>
          <div className="container relative mx-auto">
            <div className="py-16 px-4 m-auto text-center">
              <a href="/">
                <h1 className="text-white font-bold uppercase text-6xl leading-none">
                  Ozon Parser
                </h1>
              </a>
            </div>
            <Form />
            {/*<List />*/}
            {/*<Detail />*/}

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

        <section className="pb-20 bg-red-500 -mt-24">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap">
              <div className="lg:pt-12 pt-6 w-full md:w-4/12 px-4 text-center">
                <InfoTab
                  color="bg-red-400"
                  icon="fas fa-search"
                  title="Easy Search"
                  msg="Search products by site URL or Category
"
                />
              </div>

              <div className="w-full md:w-4/12 px-4 text-center">
                <InfoTab
                  color="bg-blue-400"
                  icon="fas fa-chart-line"
                  title="Price Charts"
                  msg="Price history over last several months"
                />
              </div>

              <div className="pt-6 w-full md:w-4/12 px-4 text-center">
                <InfoTab
                  color="bg-red-400"
                  icon="far fa-envelope-open"
                  title="Subscribe"
                  msg="Subscribe to receive notifications!"
                />
              </div>

            </div>
          </div>
        </section>
        
      </main>
    </>
  );
}
