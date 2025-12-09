
import os
import argparse
from sumtube.utils.config_util import print_config, interactive_set_config, get_config_json
from sumtube.podcast_summary import PodcastSummary
from sumtube.youtube_client import YouTubeClient

def main():
    parser = argparse.ArgumentParser(description='Summarize YouTube videos CLI.')

    parser.add_argument('--podcast_url', help='URL of the podcast')
    parser.add_argument('--output_dir', help='Directory to save podcast files (default is current directory)')
    parser.add_argument('--recover', help='Recover from a previous run')
    parser.add_argument('--print-config', action='store_true', help='Print current configuration')
    parser.add_argument('--set-config', action='store_true', help='Interactively set configuration')

    args = parser.parse_args()

    # If no arguments passed, or none of the valid options are used, show help
    if len(vars(args)) == 0 or not any([args.print_config, args.set_config, args.podcast_url]):
        parser.print_help()
        return

    if args.print_config:
        print_config()
        return

    if args.set_config:
        interactive_set_config()
        return

    if args.output_dir:
       output_dir = args.output_dir
    else:
        output_dir = os.path.join(os.environ.get('HOME', '.'), 'sumtube_results')

    # At this point, --podcast_url is required
    if not args.podcast_url:
        print("Error: --podcast_url is required unless --print-config or --set-config is used.")
        parser.print_help()
        return

    if args.recover:
        podcast_summary = PodcastSummary(args.podcast_url, output_dir=output_dir, recover=args.recover)
    else:
        podcast_summary = PodcastSummary(args.podcast_url, output_dir=output_dir)
    
    config_params = get_config_json()
    podcast_summary.config(**config_params)
    podcast_summary.create_summary_report()
    

if __name__ == '__main__':
    main()