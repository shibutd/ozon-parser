import React from "react";
import Form from './components/Form';

export default function App() {
  return (
    <>
      <main>
        <div className="relative pt-16 pb-32 bg-indigo-600"
            style={{
              minHeight: "75vh"
            }}>
          <div className="container relative mx-auto">
            <div className="w-full px-4 ml-auto mr-auto text-center">
              <h1 className="text-white font-bold uppercase text-6xl">
                Ozon Parser
              </h1>

            </div>
            <Form />

          </div>
          <div
            className="top-auto bottom-0 left-0 right-0 w-full absolute pointer-events-none overflow-hidden"
            style={{ height: "70px", transform: "translateZ(0)" }}
          >
            <svg
              className="absolute bottom-0 overflow-hidden"
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
                <div className="relative flex flex-col min-w-0 break-words bg-white w-full mb-8 shadow-lg rounded-lg">
                  <div className="px-4 py-5 flex-auto">
                    <div className="text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 mb-5 shadow-lg rounded-full bg-red-400">
                      <i class="fas fa-search"></i>
                    </div>
                    <h6 className="text-xl font-semibold">
                    Easy Search
                    </h6>
                    <p className="mt-2 mb-4 text-gray-600">
                      Search products by site URL <br /> or Category
                    </p>
                  </div>
                </div>
              </div>

              <div className="w-full md:w-4/12 px-4 text-center">
                <div className="relative flex flex-col min-w-0 break-words bg-white w-full mb-8 shadow-lg rounded-lg">
                  <div className="px-4 py-5 flex-auto">
                    <div className="text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 mb-5 shadow-lg rounded-full bg-blue-400">
                      <i class="fas fa-chart-line"></i>
                    </div>
                    <h6 className="text-xl font-semibold">
                      Price Charts
                    </h6>
                    <p className="mt-2 mb-4 text-gray-600">
                      Charts showing price history <br /> over last several months
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-6 w-full md:w-4/12 px-4 text-center">
                <div className="relative flex flex-col min-w-0 break-words bg-white w-full mb-8 shadow-lg rounded-lg">
                  <div className="px-4 py-5 flex-auto">
                    <div className="text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 mb-5 shadow-lg rounded-full bg-red-400">
                      <i class="far fa-envelope-open"></i>
                    </div>
                    <h6 className="text-xl font-semibold">
                      Subscribe
                    </h6>
                    <p className="mt-2 mb-4 text-gray-600">
                      Subscribe to receive notifications <br /> about price drop!
                    </p>
                  </div>
                </div>
              </div>
            </div>


          </div>
        </section>
      </main>
    </>
  );
}
