#!/usr/bin/env python


if __name__ == '__main__':
    # Initialise settings
    import sys
    sys.path.append('D:\\Programming\\settings_manager\\python')
    from settings_manager import Settings

    s = Settings()
    s.add('integer', 1)
    s.add('string1', None, data_type=str)
    s.add('float', 5.0)
    s.add('choice', 'A', choices=['A', 'B', 'C', 'D'])
    s.add('list', ['/path/to/one.txt', '/path/to/two.txt', '/path/three.txt'])
    s.add('bool', False)
    s.add('string2', 'Only if parent is enabled', data_type=str, parent='string1')
    s.add('string3', 'Only if parent is enabled', data_type=str, parent='string2')

    parser = s.as_argparser()
    args = parser.parse_args()

    print(args)
    v = vars(args)
    print(v)
    print(Settings(v))
