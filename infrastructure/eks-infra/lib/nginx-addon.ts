import { Construct } from "constructs";
import * as blueprints from "@aws-quickstart/eks-blueprints";

export interface NginxAddOnProps extends blueprints.HelmAddOnUserProps {
    version?: string;
    name?: string;
    createNamespace?: boolean;
    namespace?: string;
}

export const defaultProps: blueprints.HelmAddOnProps & NginxAddOnProps = {
    name: "nginx-addon",
    namespace: "kube-system",
    chart: "ingress-nginx",
    version: "4.11.3",
    release: "k8s-ingress",
    repository: "https://kubernetes.github.io/ingress-nginx",
    values: {
        controller: {
            ingressClass: {
                create: true,
                name: "nginx",
            },
            config: {
                // ** Use the below commented code to enable path re-writing ** //
                // "enable-rewrite-log": "true",
                // "rewrite-target": "/$2",
                "use-regex": "true",
                "ssl-redirect": "true",
                "allow-snippet-annotations": "true",
            },
            service: {
                type: 'LoadBalancer',
                annotations: {
                    "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "http",
                    "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
                    "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing",
                    "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                    "service.beta.kubernetes.io/aws-load-balancer-ssl-negotiation-policy": "ELBSecurityPolicy-TLS13-1-2-2021-06",
                    "service.beta.kubernetes.io/aws-load-balancer-ssl-cert": "arn:aws:acm:us-east-1:014648506868:certificate/44491789-1802-4436-af84-a61577274763",
                    "service.beta.kubernetes.io/aws-load-balancer-ssl-ports": "https",
                },
                serviceSpec: {
                    ports: [
                        {
                            name: 'http',
                            port: 80,
                            targetPort: 'http'
                        },
                        {
                            name: 'https',
                            port: 443,
                            targetPort: 'https'
                        }
                    ],
                    selector: {
                        'app.kubernetes.io/component': 'controller',
                        'app.kubernetes.io/instance': 'nginx-ingress',
                        'app.kubernetes.io/name': 'ingress-nginx'
                    }
                }
            },
            metrics: {
                enabled: true
            }
        }
    }
};

function populateValues(helmOptions: NginxAddOnProps): blueprints.Values {
    const values = helmOptions.values ?? {};
    return values;
}

export class NginxAddOn extends blueprints.HelmAddOn {
    readonly options: NginxAddOnProps;

    constructor(props: NginxAddOnProps) {
        super({ ...defaultProps, ...props });
        this.options = this.props as NginxAddOnProps;
    }

    deploy(clusterInfo: blueprints.ClusterInfo): void | Promise<Construct> {
        const values: blueprints.Values = populateValues(this.options);
        const chart = this.addHelmChart(clusterInfo, values);

        return Promise.resolve(chart);
    }
}
