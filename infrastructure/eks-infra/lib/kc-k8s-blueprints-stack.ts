import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { KcPlatformTeam, KcApplicationTeam } from '../teams';

export interface KcClusterProps extends cdk.StackProps {}

export class KcClusterConstruct extends Construct {
  constructor(scope: Construct, id: string, props?: KcClusterProps) {
    super(scope, id);

    const account = props?.env?.account!;
    const region = props?.env?.region!;
    const stage = scope.node.tryGetContext('stage') || 'prod'; // default to prod if not given

    // Simple defaults
    const desiredSize = 2;
    const maxSize = 4;
    const minSize = 2;

    // Node role for worker nodes
    const nodeRole = new blueprints.CreateRoleProvider(
      "kc-cluster-node-role",
      new cdk.aws_iam.ServicePrincipal('ec2.amazonaws.com'),
      [
        cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonEKSWorkerNodePolicy"),
        cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonEC2ContainerRegistryReadOnly"),
        cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonSSMManagedInstanceCore"),
        cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonEKS_CNI_Policy"),
        cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchAgentServerPolicy"),
      ]
    );

    // Managed node group config
    const mngProps: blueprints.MngClusterProviderProps = {
      version: cdk.aws_eks.KubernetesVersion.V1_28, // explicit version instead of 'auto'
      instanceTypes: [new cdk.aws_ec2.InstanceType("t3.medium")],
      amiType: cdk.aws_eks.NodegroupAmiType.AL2_X86_64,
      nodeRole: blueprints.getNamedResource("node-role") as cdk.aws_iam.Role,
      desiredSize,
      maxSize,
      minSize,
      diskSize: 20,
      nodegroupName: `eks-blueprints-mng-v1`,
    };

    // AddOns
    const ebsCsiDriverAddOn = new blueprints.addons.EbsCsiDriverAddOn({
      version: "auto",
      storageClass: "gp3",
    });

    const cloudWatchLogsAddon = new blueprints.addons.CloudWatchLogsAddon({
      logGroupPrefix: `/aws/eks/${id}`,
      logRetentionDays: 7,
    });

    // Build the EKS blueprint
    blueprints.EksBlueprint.builder()
      .account(account)
      .region(region)
      .clusterProvider(new blueprints.MngClusterProvider(mngProps))
      .resourceProvider("node-role", nodeRole)
      .teams(new KcPlatformTeam(account), new KcApplicationTeam('apps', account))
      .addOns(
        ebsCsiDriverAddOn,
        cloudWatchLogsAddon,
        new blueprints.addons.MetricsServerAddOn(),
        new blueprints.addons.ClusterAutoScalerAddOn(),
        new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      )
      .useDefaultSecretEncryption(false)
      .build(scope, id + `-${stage}-stack`);
  }
}
