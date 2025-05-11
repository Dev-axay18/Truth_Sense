import { Fragment } from 'react'
import { Menu, Transition } from '@headlessui/react'
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline'

const themes = [
  { name: 'Light', icon: SunIcon },
  { name: 'Dark', icon: MoonIcon },
  { name: 'System', icon: ComputerDesktopIcon },
]

export default function ThemeSwitcher({ currentTheme, onThemeChange }) {
  return (
    <Menu as="div" className="relative">
      <Menu.Button className="flex items-center rounded-lg bg-gray-800 p-2 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-purple-500">
        <span className="sr-only">Open theme menu</span>
        {currentTheme === 'Light' ? (
          <SunIcon className="h-5 w-5" aria-hidden="true" />
        ) : currentTheme === 'Dark' ? (
          <MoonIcon className="h-5 w-5" aria-hidden="true" />
        ) : (
          <ComputerDesktopIcon className="h-5 w-5" aria-hidden="true" />
        )}
      </Menu.Button>
      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-lg bg-gray-800 py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          {themes.map((theme) => (
            <Menu.Item key={theme.name}>
              {({ active }) => (
                <button
                  onClick={() => onThemeChange(theme.name)}
                  className={`${
                    active ? 'bg-gray-700' : ''
                  } ${
                    currentTheme === theme.name ? 'text-purple-400' : 'text-gray-300'
                  } group flex w-full items-center px-4 py-2 text-sm`}
                >
                  <theme.icon
                    className="mr-3 h-5 w-5"
                    aria-hidden="true"
                  />
                  {theme.name}
                </button>
              )}
            </Menu.Item>
          ))}
        </Menu.Items>
      </Transition>
    </Menu>
  )
} 