from spylt.cli import create_cli

parser = create_cli()
args = parser.parse_args()
args.func(args)
