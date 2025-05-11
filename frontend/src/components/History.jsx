import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'

export default function History({ isOpen, onClose, history, onSelectHistory }) {
  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-500"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-500"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-md">
                  <div className="flex h-full flex-col overflow-y-scroll bg-gray-900 shadow-xl">
                    <div className="px-4 py-6 sm:px-6">
                      <div className="flex items-start justify-between">
                        <Dialog.Title className="text-base font-semibold leading-6 text-white">
                          Analysis History
                        </Dialog.Title>
                        <div className="ml-3 flex h-7 items-center">
                          <button
                            type="button"
                            className="relative rounded-md bg-gray-800 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                            onClick={onClose}
                          >
                            <span className="absolute -inset-2.5" />
                            <span className="sr-only">Close panel</span>
                            <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="relative mt-6 flex-1 px-4 sm:px-6">
                      <div className="space-y-4">
                        {history.map((item, index) => (
                          <div
                            key={index}
                            onClick={() => onSelectHistory(item)}
                            className="cursor-pointer rounded-lg bg-gray-800 p-4 hover:bg-gray-700 transition-all"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-400">
                                {new Date(item.timestamp).toLocaleString()}
                              </span>
                              <span
                                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                  item.classification === 'True'
                                    ? 'bg-green-100 text-green-800'
                                    : item.classification === 'Fake'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-yellow-100 text-yellow-800'
                                }`}
                              >
                                {item.classification}
                              </span>
                            </div>
                            <p className="mt-2 text-sm text-white line-clamp-2">
                              {item.content}
                            </p>
                            <div className="mt-2 flex items-center space-x-4 text-xs text-gray-400">
                              <span>Confidence: {item.confidence_score}%</span>
                              <span>•</span>
                              <span>{item.country_of_origin}</span>
                              <span>•</span>
                              <span>
                                {item.is_verified ? 'Verified' : 'Unverified'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
} 